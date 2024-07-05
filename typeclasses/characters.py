"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent
from world.data import STATS


class Character(ObjectParent, DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_post_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def at_object_creation(self):
        super().at_object_creation()

        # initialize attributes
        self.db.stats = STATS

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """
        We make sure to look around after a move.

        """
        # Same logic as parent DefaultCharacter, but
        # pass in the kwargs for proper multi-session handling
        if self.location.access(self, "view"):
            self.msg(text=(self.at_look(self.location, **kwargs), {"type": "look"}))

    def at_post_puppet(self, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.

        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call
        Notes:

            You can use the session argument from kwargs to get the
            session when executed from a command.

            Otherwise, you can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Session
            puppeting this Object.

        """
        self.msg(_("\nYou become |c{name}|n.\n").format(name=self.key))
        self.msg((self.at_look(self.location, **kwargs), {"type": "look"}), options=None)

        def message(obj, from_obj):
            obj.msg(
                _("{name} has entered the game.").format(name=self.get_display_name(obj)),
                from_obj=from_obj,
            )

        self.location.for_contents(message, exclude=[self], from_obj=self)

    def get_display_name(self, looker=None, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object. If not given, `.name` will be
                returned, which can in turn be used to display colored data.

        Returns:
            str: A name to display for this object. This can contain color codes and may
                be customized based on `looker`. By default this contains the `.key` of the object,
                followed by the DBREF if this user is privileged to control said object.

        Notes:
            This function could be extended to change how object names appear to users in character,
            but be wary. This function does not change an object's keys or aliases when searching,
            and is expected to produce something useful for builders.

        """
        if looker and self.locks.check_lockstring(looker, "perm(Builder)"):
            return "{}(#{})".format(self.db.moniker or self.name, self.id)

        return self.db.moniker or self.name

    def get_display_shortdesc(self, looker=None, **kwargs):
        if self.db.shortdesc:
            return self.db.shortdesc
        else:
            return "Use '+short <description>' to set a description."

    def format_idle_time(self, looker, **kwargs):
        # If the character is the looker, show 0s.
        if self == looker:
            return "|g0s|n"
        time = self.idle_time or self.connection_time
        if time is None:
            return "|g0s|n"
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        # round seconds
        seconds = int(round(seconds, 0))
        minutes = int(round(minutes, 0))
        hours = int(round(hours, 0))
        days = int(round(days, 0))

        if days > 0:
            time_str = f"|x{days}d|n"
        elif hours > 0:
            time_str = f"|x{hours}h|n"
        elif minutes > 0:
            if minutes > 10 and minutes < 15:
                time_str = f"|G{minutes}m|n"
            elif minutes > 15 and minutes < 20:
                time_str = f"|y{minutes}m|n"
            elif minutes > 20 and minutes < 30:
                time_str = f"|r{minutes}m|n"
            elif minutes > 30 and minutes:
                time_str = f"|r{minutes}m|n"
            else:
                time_str = f"|g{minutes}m|n"
        elif seconds > 0:
            time_str = f"|g{seconds}s|n"
        return time_str.strip()

